# -*- coding: utf-8 -*-
from api import ApiError, get_day_menu
from constants import WEB_URL, WEEKDAYS_CN, WEEKDAYS_EN, CYAN, BOLD, DIM
from utils import (c, die, resolve_school, resolve_date, week_for, print_meal, filter_meals,
                   parse_allergen_filters, dump_json)


def cmd_menu(args):
    school = resolve_school(args.school)
    date = resolve_date(args)
    week = week_for(date)
    try:
        menu = get_day_menu(week["id"], date.weekday(), school)
    except ApiError as e:
        die(str(e))
    meals = filter_meals(menu, args.meal)
    avoid = parse_allergen_filters(args.exclude)
    if avoid:
        for m in meals:
            m["dishes"] = [d for d in m["dishes"] if not args.hide or not set(d["allergen_codes"]) & avoid]

    if args.json:
        dump_json({"date": date, "weekday": WEEKDAYS_CN[date.weekday()], "school": school,
                   "week_id": week["id"], "week_title": week["title"], "meals": meals})
        return

    wd = WEEKDAYS_EN[date.weekday()] if args.en else WEEKDAYS_CN[date.weekday()]
    head = f"📅 {date.isoformat()} {wd} · {school if not args.en else ('Middle/High' if school == '中学' else 'Primary')}"
    print(c(head, CYAN + BOLD) + c(f"   week #{week['id']} ({week['title']})", DIM))
    print()
    for m in meals:
        print_meal(m, en=args.en, show_allergens=not args.no_allergens, avoid=avoid)
        print()
    if args.link:
        print(c(WEB_URL.format(week_id=week["id"]), DIM))
