# -*- coding: utf-8 -*-
import datetime

from api import ApiError, list_weeks
from constants import WEB_URL, BOLD, DIM, GREEN
from utils import c, die, dump_json


def cmd_weeks(args):
    try:
        weeks = list_weeks()
    except ApiError as e:
        die(str(e))
    weeks = weeks[: args.limit] if args.limit else weeks
    if args.json:
        dump_json(weeks)
        return
    today = datetime.date.today()
    print(c(f"{'ID':<6}{'Week':<26}School", BOLD))
    for w in weeks:
        line = f"{w['id']:<6}{w['title']:<26}{w['school']}"
        if w["start"] <= today <= w["end"]:
            line = c(line + "  ◀ this week", GREEN)
        print(line)
    if args.link and weeks:
        print(c(WEB_URL.format(week_id=weeks[0]["id"]), DIM))
