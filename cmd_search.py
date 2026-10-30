# -*- coding: utf-8 -*-
import datetime

from api import ApiError, get_week_menu
from constants import WEEKDAYS_CN, BOLD, DIM, CYAN
from utils import c, die, resolve_school, resolve_date, week_for, dump_json


def cmd_search(args):
    school = resolve_school(args.school)
    week = week_for(resolve_date(args))
    try:
        days = get_week_menu(week["id"], school)
    except ApiError as e:
        die(str(e))
    kw = args.keyword.lower()
    hits = []
    for i, day in enumerate(days):
        for m in day["meals"]:
            for d in m["dishes"]:
                if kw in d["name"].lower() or kw in d["name_en"].lower():
                    hits.append({"date": week["start"] + datetime.timedelta(days=i),
                                 "weekday": WEEKDAYS_CN[i], "meal": m["name"], **d})
    if args.json:
        dump_json(hits)
        return
    if not hits:
        print(f"本周（{week['title']}）没有找到「{args.keyword}」")
        return
    print(c(f"🔎 「{args.keyword}」 在 {week['title']} 出现 {len(hits)} 次", CYAN + BOLD))
    for h in hits:
        print(f"  {h['date'].strftime('%m-%d')} {h['weekday'].replace('星期', '周')} {h['meal']:<4} "
              f"{c(h['name'], BOLD)} {c(h['name_en'], DIM)} {c(h['calorie'], DIM)}")
