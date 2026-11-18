# -*- coding: utf-8 -*-
"""THISDL 食堂菜单接口（无需登录）。"""
import datetime
import hashlib
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

from constants import API_BASE, HEADERS, WEEKDAYS_CN, MEALS, DISH_TYPES, ALLERGENS


class ApiError(RuntimeError):
    pass


CACHE_DIR = Path(os.environ.get("DLMENU_CACHE_DIR", Path.home() / ".dlmenu" / "cache"))
CACHE_TTL = int(os.environ.get("DLMENU_CACHE_TTL", "1800"))  # 秒，设为 0 关闭缓存


def _cache_path(path, params):
    key = hashlib.sha1(json.dumps([path, params], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return CACHE_DIR / f"{key}.json"


def _get(path, params=None, timeout=15):
    params = params or {}
    cp = _cache_path(path, params)
    if CACHE_TTL > 0 and cp.is_file() and time.time() - cp.stat().st_mtime < CACHE_TTL:
        try:
            return json.loads(cp.read_text("utf-8"))
        except (OSError, ValueError):
            pass
    data = _fetch(path, params, timeout)
    if CACHE_TTL > 0:
        try:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            cp.write_text(json.dumps(data, ensure_ascii=False), "utf-8")
        except OSError:
            pass
    return data


def clear_cache():
    n = 0
    if CACHE_DIR.is_dir():
        for f in CACHE_DIR.glob("*.json"):
            f.unlink(missing_ok=True); n += 1
    return n


def _fetch(path, params, timeout, retries=3):
    for attempt in range(retries):
        try:
            resp = requests.get(API_BASE + path, params=params, headers=HEADERS, timeout=timeout)
            resp.raise_for_status()
            body = resp.json()
            break
        except requests.RequestException as e:
            if attempt == retries - 1:
                raise ApiError(f"网络请求失败: {e}") from e
            time.sleep(0.8 * (attempt + 1))
        except ValueError as e:
            raise ApiError("接口返回的不是 JSON") from e
    if body.get("code") != 200:
        raise ApiError(body.get("message") or f"接口返回 code={body.get('code')}")
    return body["data"]


def parse_day_start(s):
    """'261026' -> date(2026, 10, 26)"""
    return datetime.date(2000 + int(s[:2]), int(s[2:4]), int(s[4:6]))


def list_weeks():
    weeks = _get("api/info/canteen_week_list")
    out = []
    for w in weeks:
        try:
            start = parse_day_start(w["day_start"])
        except (KeyError, ValueError, TypeError):
            continue
        out.append({"id": w["id"], "school": w.get("school", ""), "title": w.get("week_title", ""),
                    "start": start, "end": start + datetime.timedelta(days=6)})
    out.sort(key=lambda w: w["start"], reverse=True)
    return out


def find_week(date, weeks=None):
    weeks = weeks if weeks is not None else list_weeks()
    for w in weeks:
        if w["start"] <= date <= w["end"]:
            return w
    return None


TITLE_DATE_RE = re.compile(r"(\d{4})\.(\d{1,2})\.(\d{1,2})\s*-\s*(\d{4})\.(\d{1,2})\.(\d{1,2})")

# 周列表接口可能落后于菜单本身（新的那一周已上传菜品，但还没进周列表），
# 这时按 id 往后试探，用 canteen_item_list 的 title_date 反推日期区间。
# 开销 = 实际存在但未列入的周数（找到/越过目标即停），与列表停更多久无关；
# 历史 id 有跳号（如 3 → 5），所以允许连续漏几个再放弃。
WEEK_PROBE_LIMIT = int(os.environ.get("DLMENU_WEEK_PROBE", "26"))
WEEK_PROBE_MISSES = 2


def parse_title_date(text):
    """'2026.11.16-2026.11.22' -> (date(2026, 11, 16), date(2026, 11, 22))"""
    m = TITLE_DATE_RE.search(text or "")
    if not m:
        return None
    try:
        start = datetime.date(*map(int, m.groups()[:3]))
        end = datetime.date(*map(int, m.groups()[3:]))
    except ValueError:
        return None
    return (start, end) if start <= end else None


def probe_week(date, weeks=None, limit=None):
    """周列表里查不到时，按 id 试探后面的周（是否真的存在以接口返回为准）。

    正常情况只发 1 次请求；请求次数只跟“存在但没列出来的周数”有关，
    跟周列表停更多久无关，最多 limit 次。
    """
    limit = WEEK_PROBE_LIMIT if limit is None else limit
    weeks = weeks if weeks is not None else list_weeks()
    if not weeks or limit <= 0 or date <= weeks[0]["end"]:
        return None
    last_id = max(w["id"] for w in weeks)
    misses = 0
    for step in range(1, limit + 1):
        week_id = last_id + step
        try:
            data = _get("api/info/canteen_item_list",
                        {"page": 1, "page_size": 1, "week_id": week_id,
                         "week": WEEKDAYS_CN[0], "remark": "中学"})
        except ApiError:
            misses += 1
            if misses >= WEEK_PROBE_MISSES:
                return None  # id 已经用尽，后面的周不会存在
            continue
        misses = 0
        rng = parse_title_date(data.get("title_date"))
        if not rng:
            continue
        start, end = rng
        if start > date:
            return None  # 已经越过目标周，说明那一周确实没发布
        if start <= date <= end:
            return {"id": week_id, "school": weeks[0].get("school", ""),
                    "title": data.get("title_date", ""), "start": start, "end": end}
    return None


def _flatten(value):
    """接口里大多数类别是 [{"row": [...]}, ...]，清真午餐是平铺的列表。"""
    items = []
    for entry in value or []:
        if isinstance(entry, dict) and "row" in entry:
            items.extend(entry["row"] or [])
        elif isinstance(entry, dict):
            items.append(entry)
    return [i for i in items if i.get("name_sc") and i.get("name_sc") != "空占位"]


def _dish(raw, category_cn, category_en):
    codes = [int(c) for c in str(raw.get("allergen", "")).split(",") if c.strip().isdigit()]
    return {
        "name": raw.get("name_sc", "").strip(),
        "name_en": raw.get("name_en", "").strip(),
        "category": category_cn,
        "category_en": category_en,
        "calorie": raw.get("calorie", "").strip(),
        "nutritional": raw.get("nutritional", "").strip(),
        "allergen_codes": codes,
        "allergens": [ALLERGENS.get(c, (f"#{c}", f"#{c}"))[0] for c in codes],
        "allergens_en": [ALLERGENS.get(c, (f"#{c}", f"#{c}"))[1] for c in codes],
        "taste": raw.get("taste", "").strip(),
        "stall": raw.get("stall", "").strip(),
    }


def get_day_menu(week_id, weekday_index, school="中学"):
    """返回某一天的菜单：{"date_title", "meals": [{key, name, name_en, dishes: [...]}, ...]}"""
    data = _get("api/info/canteen_item_list", {
        "page": 1, "page_size": 150, "week_id": week_id,
        "week": WEEKDAYS_CN[weekday_index], "remark": school,
    })
    meals = []
    for key, cn, en, prefix, _color, _t in MEALS:
        dishes = []
        if prefix.endswith("_"):
            for suffix, (tcn, ten) in DISH_TYPES.items():
                for raw in _flatten(data.get(prefix + suffix)):
                    dishes.append(_dish(raw, tcn, ten))
        else:
            for raw in _flatten(data.get(prefix)):
                tcn = raw.get("dish_type", "") or cn
                ten = next((v[1] for v in DISH_TYPES.values() if v[0] == tcn), en)
                dishes.append(_dish(raw, tcn, ten))
        meals.append({"key": key, "name": cn, "name_en": en, "dishes": dishes})
    return {"week_title": data.get("title_date", ""), "meals": meals}


def get_week_menu(week_id, school="中学"):
    with ThreadPoolExecutor(max_workers=3) as pool:
        return list(pool.map(lambda i: get_day_menu(week_id, i, school), range(7)))
