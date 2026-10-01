import unittest

from amounts import classify_amount


class AmountTests(unittest.TestCase):
    def test_missing_and_zero_are_distinct(self):
        self.assertEqual(classify_amount(None), "missing")
        self.assertEqual(classify_amount(0), "zero")

    def test_sign_categories(self):
        self.assertEqual(classify_amount(2), "positive")
        self.assertEqual(classify_amount(-2), "negative")


if __name__ == "__main__":
    unittest.main()
