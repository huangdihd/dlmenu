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

    def test_parse_title_date(self):
        self.assertEqual(api.parse_title_date("2026.11.16-2026.11.22"),
                         (datetime.date(2026, 11, 16), datetime.date(2026, 11, 22)))
        self.assertIsNone(api.parse_title_date(""))
        self.assertIsNone(api.parse_title_date("2026.11.23-2026.11.16"))

    def _fake_weeks(self):
        return [{"id": 149, "school": "稻香湖", "title": "2026.11.09-2026.11.15",
                 "start": datetime.date(2026, 11, 9), "end": datetime.date(2026, 11, 15)}]

    def _patch_get(self, mapping):
        original = api._get
        calls = []

        def fake_get(path, params=None, timeout=15):
            week_id = (params or {}).get("week_id")
            calls.append(week_id)
            if week_id not in mapping:
                raise api.ApiError(f"week {week_id} not found")
            return {"title_date": mapping[week_id]}

        api._get = fake_get
        self.addCleanup(setattr, api, "_get", original)
        return calls

    def test_probe_week_finds_unlisted_week(self):
        self._patch_get({150: "2026.11.16-2026.11.22", 151: "2026.11.23-2026.11.29"})
        week = api.probe_week(datetime.date(2026, 11, 18), self._fake_weeks())
        self.assertEqual(week["id"], 150)
        self.assertEqual(week["start"], datetime.date(2026, 11, 16))
        self.assertEqual(week["end"], datetime.date(2026, 11, 22))
        self.assertEqual(week["title"], "2026.11.16-2026.11.22")

    def test_probe_week_stops_when_week_missing(self):
        self._patch_get({151: "2026.11.23-2026.11.29"})
        self.assertIsNone(api.probe_week(datetime.date(2026, 12, 20), self._fake_weeks()))

    def test_probe_week_tolerates_gapped_ids(self):
        # 历史 id 有跳号，150 不存在但 151 才是下一周
        calls = self._patch_get({151: "2026.11.23-2026.11.29"})
        week = api.probe_week(datetime.date(2026, 11, 25), self._fake_weeks())
        self.assertEqual(week["id"], 151)
        self.assertEqual(calls, [150, 151])

    def test_probe_week_skips_known_range(self):
        self._patch_get({150: "2026.11.16-2026.11.22"})
        self.assertIsNone(api.probe_week(datetime.date(2026, 11, 10), self._fake_weeks()))

    def test_probe_week_cost_is_bounded(self):
        # 只有 150 真实存在：再往后连续两个 id 不存在就放弃，
        # 与列表停更多久无关（不会随日期推移无限试探）。
        calls = self._patch_get({150: "2026.11.16-2026.11.22"})
        self.assertIsNone(api.probe_week(datetime.date(2027, 6, 1), self._fake_weeks()))
        self.assertEqual(calls, [150, 151, 152])

    def test_probe_week_respects_limit(self):
        mapping = {150 + i: "2026.11.16-2026.11.22" for i in range(10)}
        calls = self._patch_get(mapping)
        self.assertIsNone(api.probe_week(datetime.date(2027, 6, 1), self._fake_weeks(), limit=3))
        self.assertEqual(calls, [150, 151, 152])

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
