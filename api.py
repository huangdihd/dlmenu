# -*- coding: utf-8 -*-
"""THISDL 食堂菜单接口（无需登录）。"""
import datetime
import hashlib
import json
import os
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
