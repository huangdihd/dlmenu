# -*- coding: utf-8 -*-
import datetime
import json
import os
import re
import sys
import unicodedata

from constants import (RESET, BOLD, DIM, RED, YELLOW, MEALS, SCHOOLS, WEEKDAYS_CN, WEEKDAYS_EN, ALLERGENS)
from api import ApiError, list_weeks, find_week

ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
MEAL_ICONS = {"breakfast": "🍳", "morning": "🍪", "lunch": "🍱", "muslim": "🥘",
              "afternoon": "🍰", "supper": "🍲", "night": "🌙"}
WEEKDAY_ALIASES = {}
for i, (cn, en) in enumerate(zip(WEEKDAYS_CN, WEEKDAYS_EN)):
    for a in (cn, cn.replace("星期", "周"), en.lower(), en[:3].lower(), str(i + 1)):
        WEEKDAY_ALIASES[a] = i
WEEKDAY_ALIASES["周天"] = WEEKDAY_ALIASES["星期天"] = 6


def use_color():
    return sys.stdout.isatty() and not os.environ.get("NO_COLOR") and not os.environ.get("DLMENU_NONINTERACTIVE")


def c(text, color):
    return f"{color}{text}{RESET}" if use_color() else text


def width(s):
    s = ANSI.sub("", s)
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in s)


def pad(s, w):
    return s + " " * max(0, w - width(s))


def die(msg, code=1):
    print(c(f"✗ {msg}", RED), file=sys.stderr)
    sys.exit(code)


def resolve_school(name):
    name = (name or os.environ.get("DLMENU_SCHOOL") or "中学").strip().lower()
    if name not in SCHOOLS:
        die(f"未知校区/学部: {name}（可用: 中学 / 小学）")
    return SCHOOLS[name]


def resolve_date(args):
    today = datetime.date.today()
    if getattr(args, "date", None):
        try:
            return datetime.date.fromisoformat(args.date)
        except ValueError:
            die(f"日期格式不对: {args.date}，应为 YYYY-MM-DD")
    if getattr(args, "tomorrow", False):
        return today + datetime.timedelta(days=1)
    if getattr(args, "day", None):
        key = args.day.strip().lower()
        if key not in WEEKDAY_ALIASES:
            die(f"看不懂星期几: {args.day}（例如 mon / 周一 / 1）")
        monday = today - datetime.timedelta(days=today.weekday())
        return monday + datetime.timedelta(days=WEEKDAY_ALIASES[key])
    return today


def week_for(date):
    try:
        week = find_week(date)
    except ApiError as e:
        die(str(e))
    if not week:
        die(f"食堂还没有发布 {date.isoformat()} 所在那一周的菜单")
    return week


def parse_allergen_filters(values):
    """把 -x 参数（中文名 / 英文名 / 编号）转成编号集合。"""
    codes = set()
    for v in values or []:
        for part in re.split(r"[,，\s]+", v.strip()):
            if not part:
                continue
            if part.isdigit():
                codes.add(int(part)); continue
            hit = [k for k, (cn, en) in ALLERGENS.items()
                   if part.lower() in (cn.rstrip("?"), en.rstrip("?").lower())]
            if not hit:
                die(f"不认识的过敏原: {part}（用 `dlmenu allergens` 查看全部）")
            codes.update(hit)
    return codes


def dish_line(d, en=False, show_allergens=True, avoid=frozenset(), name_w=0):
    primary, secondary = (d["name_en"], d["name"]) if en else (d["name"], d["name_en"])
    cat = d["category_en"] if en else d["category"]
    bad = avoid and set(d["allergen_codes"]) & avoid
    name = c(primary, RED + BOLD) if bad else c(primary, BOLD)
    parts = [c(pad(f"[{cat}]", 9 if not en else 19), DIM), pad(name, name_w)]
    if d["calorie"]:
        parts.append(c(pad(d["calorie"], 9), YELLOW))
    line = "  " + " ".join(parts)
    if secondary:
        line += " " + c(secondary, DIM)
    if show_allergens and d["allergens"]:
        names = d["allergens_en"] if en else d["allergens"]
        line += "  " + c("⚠ " + " ".join(names), RED if bad else DIM)
    return line


def print_meal(meal, en=False, show_allergens=True, avoid=frozenset()):
    color = next(m[4] for m in MEALS if m[0] == meal["key"])
    title = f"{MEAL_ICONS.get(meal['key'], '•')} {meal['name_en'] if en else meal['name']}"
    if not en:
        title += f" {meal['name_en']}"
    print(c(title, color + BOLD))
    if not meal["dishes"]:
        print(c("  （无）" if not en else "  (none)", DIM))
        return
    w = max(width(d["name_en"] if en else d["name"]) for d in meal["dishes"]) + 1
    for d in meal["dishes"]:
        print(dish_line(d, en, show_allergens, avoid, w))


def filter_meals(menu, meal_keys):
    if not meal_keys:
        return [m for m in menu["meals"] if m["dishes"]] or menu["meals"]
    return [m for m in menu["meals"] if m["key"] in meal_keys]


def dump_json(obj):
    def default(o):
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        raise TypeError
    print(json.dumps(obj, ensure_ascii=False, indent=2, default=default))
