# -*- coding: utf-8 -*-
import datetime

from api import ApiError, get_week_menu
from constants import WEEKDAYS_CN, WEEKDAYS_EN, CYAN, BOLD, DIM, GREEN, BLUE, YELLOW
from utils import c, die, resolve_school, resolve_date, week_for, width, pad, dump_json

MAIN_TYPES = ("荤菜", "半荤菜", "蛋类菜", "素菜")


def cmd_week(args):
    school = resolve_school(args.school)
    date = resolve_date(args)
    if args.next:
        date += datetime.timedelta(days=7)
    week = week_for(date)
    try:
        days = get_week_menu(week["id"], school)
    except ApiError as e:
        die(str(e))

    if args.json:
        dump_json({"week_id": week["id"], "week_title": week["title"], "school": school,
                   "days": [{"date": week["start"] + datetime.timedelta(days=i),
                             "weekday": WEEKDAYS_CN[i], "meals": d["meals"]} for i, d in enumerate(days)]})
        return

    print(c(f"🗓  {week['title']} · {school}", CYAN + BOLD) + c(f"   week #{week['id']}", DIM))
    today = datetime.date.today()
    keys = args.meal or ["lunch", "supper"]
    colors = {"breakfast": YELLOW, "lunch": GREEN, "supper": BLUE}
    for i, day in enumerate(days):
        d = week["start"] + datetime.timedelta(days=i)
        label = f"{WEEKDAYS_EN[i][:3] if args.en else WEEKDAYS_CN[i].replace('星期', '周')} {d.strftime('%m-%d')}"
        mark = " ◀ today" if d == today else ""
        print()
        print(c(label + mark, BOLD))
        any_dish = False
        for m in day["meals"]:
            if m["key"] not in keys or not m["dishes"]:
                continue
            any_dish = True
            mains = [x for x in m["dishes"] if x["category"] in MAIN_TYPES] or m["dishes"]
            names = " · ".join(x["name_en"] if args.en else x["name"] for x in mains)
            mname = m["name_en"] if args.en else m["name"]
            print(f"  {c(pad(mname, 10), colors.get(m['key'], ''))}{names}")
        if not any_dish:
            print(c("  （无）", DIM))
