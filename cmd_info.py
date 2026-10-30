# -*- coding: utf-8 -*-
import datetime

from api import ApiError, get_day_menu
from constants import logo, MEALS, WEEKDAYS_CN, ORANGE, GREEN, YELLOW, CYAN, BOLD, DIM, RESET
from utils import c, die, resolve_school, week_for, pad, use_color, ANSI, MEAL_ICONS

MAIN_TYPES = ("荤菜", "半荤菜", "蛋类菜", "素菜", "中式", "西式")


def next_meal(meals, now):
    """当前时间之后最近的一餐（有菜的），过了夜宵就返回 None。"""
    order = [m for m in MEALS if m[0] not in ("muslim",)]
    cur = None
    for key, *_rest, start in order:
        h, mi = map(int, start.split(":"))
        if now.time() < datetime.time(h, mi):
            cur = key
            break
    for m in meals:
        if m["key"] == cur and m["dishes"]:
            return m
    if cur:
        idx = [m[0] for m in order].index(cur)
        for key in [m[0] for m in order][idx + 1:]:
            for m in meals:
                if m["key"] == key and m["dishes"]:
                    return m
    return None


def cmd_info(args):
    school = resolve_school(getattr(args, "school", None))
    now = datetime.datetime.now()
    today = now.date()
    week = week_for(today)
    try:
        menu = get_day_menu(week["id"], today.weekday(), school)
    except ApiError as e:
        die(str(e))
    meals = menu["meals"]
    nm = next_meal(meals, now)

    def kcal(m):
        total = 0
        for d in m["dishes"]:
            num = "".join(ch for ch in d["calorie"] if ch.isdigit())
            total += int(num) if num else 0
        return total

    info = [
        f"🍽  {c('THISDL Canteen', ORANGE + BOLD)}",
        "-" * 30,
        f"Date      : {today.isoformat()} {WEEKDAYS_CN[today.weekday()]}",
        f"School    : {school}",
        f"Week      : #{week['id']} ({week['title']})",
    ]
    for key in ("breakfast", "lunch", "supper"):
        m = next(x for x in meals if x["key"] == key)
        info.append(f"{pad(m['name_en'], 10)}: {c(str(len(m['dishes'])) + ' dishes', GREEN)}"
                    + (c(f" · ~{kcal(m)} kcal", DIM) if m["dishes"] else ""))
    if nm:
        mains = [d for d in nm["dishes"] if d["category"] in MAIN_TYPES] or nm["dishes"]
        info.append(f"Next Meal : {c(MEAL_ICONS.get(nm['key'], '') + ' ' + nm['name'] + ' ' + nm['name_en'], CYAN)}")
        for d in mains[:4]:
            info.append(f"            {c('•', YELLOW)} {d['name']} {c(d['name_en'], DIM)}")
    else:
        info.append(f"Next Meal : {c('今天的饭都吃完啦，明天见', CYAN)}")

    rows = max(len(logo), len(info))
    for i in range(rows):
        left = logo[i] if i < len(logo) else " " * 12
        right = info[i] if i < len(info) else ""
        if not use_color():
            left = ANSI.sub("", left)
        print(f"{pad(left, 12)}  {right}")
