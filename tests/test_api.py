import datetime
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import api  # noqa: E402


class ApiHelpersTest(unittest.TestCase):
    def test_parse_day_start(self):
        self.assertEqual(api.parse_day_start("261026"), datetime.date(2026, 10, 26))

    def test_find_week(self):
        weeks = [{"id": 2, "start": datetime.date(2026, 11, 2), "end": datetime.date(2026, 11, 8)},
                 {"id": 1, "start": datetime.date(2026, 10, 26), "end": datetime.date(2026, 11, 1)}]
        self.assertEqual(api.find_week(datetime.date(2026, 10, 30), weeks)["id"], 1)
        self.assertEqual(api.find_week(datetime.date(2026, 11, 8), weeks)["id"], 2)
        self.assertIsNone(api.find_week(datetime.date(2026, 12, 1), weeks))

    def test_flatten_skips_placeholders(self):
        grouped = [{"row": [{"name_sc": "米饭"}, {"name_sc": "空占位"}]}, {"row": [{"name_sc": "馒头"}]}]
        self.assertEqual([d["name_sc"] for d in api._flatten(grouped)], ["米饭", "馒头"])
        self.assertEqual(len(api._flatten([{"name_sc": "水煮鸡片"}])), 1)

    def test_dish_allergens(self):
        d = api._dish({"name_sc": "猪肉茴香包", "name_en": "Pork Buns", "calorie": "213Kcal",
                       "allergen": "5,3"}, "中式", "Chinese style")
        self.assertEqual(d["allergens"], ["小麦", "猪肉"])
        self.assertEqual(d["allergen_codes"], [5, 3])


if __name__ == "__main__":
    unittest.main()
