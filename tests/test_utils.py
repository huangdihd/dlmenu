import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import utils  # noqa: E402


class UtilsTest(unittest.TestCase):
    def test_width_counts_cjk_as_two(self):
        self.assertEqual(utils.width("米饭"), 4)
        self.assertEqual(utils.width("rice"), 4)

    def test_allergen_filters(self):
        self.assertEqual(utils.parse_allergen_filters(["花生", "shrimp", "3"]), {23, 32, 3})
        self.assertEqual(utils.parse_allergen_filters(["花生,虾"]), {23, 32})

    def test_school_alias(self):
        self.assertEqual(utils.resolve_school("primary"), "小学")
        self.assertEqual(utils.resolve_school("中学"), "中学")


if __name__ == "__main__":
    unittest.main()
