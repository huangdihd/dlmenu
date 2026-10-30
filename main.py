#! python3
# -*- coding: utf-8 -*-
import argparse
import signal

__version__ = "1.0.0"

from cmd_info import cmd_info
from cmd_menu import cmd_menu
from cmd_week import cmd_week
from cmd_weeks import cmd_weeks
from cmd_search import cmd_search
from cmd_allergens import cmd_allergens
from cmd_cache import cmd_cache

MEAL_KEYS = ["breakfast", "morning", "lunch", "muslim", "afternoon", "supper", "night"]

EPILOG = """\
examples:
  dlmenu                   Neofetch-style overview of today's canteen
  dlmenu menu              Show today's full menu
  dlmenu menu -t           Show tomorrow's menu
  dlmenu menu -D fri       Show this Friday's menu (mon..sun / 周一..周日 / 1..7)
  dlmenu menu -d 2026-11-03
                           Show the menu for a specific date
  dlmenu menu -m lunch supper
                           Show only lunch and supper
  dlmenu menu -x 花生 虾   Mark dishes containing peanut or shrimp
  dlmenu menu -x peanut --hide
                           Hide dishes containing peanut
  dlmenu menu --en         Show the menu in English
  dlmenu menu -S 小学      Show the primary-school menu (default: 中学)
  dlmenu week              This week's lunch and supper at a glance
  dlmenu week -n           Next week's menu (once it is published)
  dlmenu search 鸡         Search this week's dishes by name (CN or EN)
  dlmenu weeks             List published menu weeks and their IDs
  dlmenu allergens         List allergen codes
  dlmenu clear-cache       Delete cached responses (cached for 30 min)
  dlmenu mcp               Start the MCP server over stdio

Add --json to menu / week / weeks / search / allergens for machine-readable output.
Set DLMENU_SCHOOL=小学 to change the default school.
"""


def add_common(p, date=True):
    p.add_argument("-S", "--school", type=str, metavar="SCHOOL", help="中学 (default) or 小学")
    p.add_argument("--json", action="store_true", help="Output JSON")
    if date:
        g = p.add_mutually_exclusive_group()
        g.add_argument("-t", "--tomorrow", action="store_true", help="Use tomorrow")
        g.add_argument("-d", "--date", type=str, metavar="YYYY-MM-DD", help="Use a specific date")
        g.add_argument("-D", "--day", type=str, metavar="WEEKDAY", help="A day of this week, e.g. fri / 周五 / 5")


def main():
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    parser = argparse.ArgumentParser(
        prog="dlmenu",
        description="🍱 A neofetch-style CLI for the THISDL canteen menu",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-v", "--version", action="version", version=f"dlmenu {__version__}")
    parser.add_argument("-S", "--school", type=str, metavar="SCHOOL", help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="command", metavar="")

    p_info = sub.add_parser("info", help="Neofetch-style overview of today (default)")
    p_info.add_argument("-S", "--school", type=str, metavar="SCHOOL", help="中学 (default) or 小学")

    p_menu = sub.add_parser("menu", help="Show a day's full menu")
    add_common(p_menu)
    p_menu.add_argument("-m", "--meal", nargs="+", choices=MEAL_KEYS, metavar="MEAL",
                        help="Only these meals: " + ", ".join(MEAL_KEYS))
    p_menu.add_argument("-x", "--exclude", nargs="+", metavar="ALLERGEN",
                        help="Mark dishes containing these allergens (name, English name or code)")
    p_menu.add_argument("--hide", action="store_true", help="With -x, hide those dishes instead of marking them")
    p_menu.add_argument("--en", action="store_true", help="English names first")
    p_menu.add_argument("--no-allergens", action="store_true", help="Don't show allergens")
    p_menu.add_argument("-l", "--link", action="store_true", help="Also print the web page link")

    p_week = sub.add_parser("week", help="Show this week's menu at a glance")
    add_common(p_week)
    p_week.add_argument("-n", "--next", action="store_true", help="Next week")
    p_week.add_argument("-m", "--meal", nargs="+", choices=MEAL_KEYS, metavar="MEAL",
                        help="Meals to show (default: lunch supper)")
    p_week.add_argument("--en", action="store_true", help="English names")

    p_weeks = sub.add_parser("weeks", help="List published menu weeks and their IDs")
    p_weeks.add_argument("-l", "--limit", type=int, metavar="N", help="Show only the latest N weeks")
    p_weeks.add_argument("--link", action="store_true", help="Print the web link of the latest week")
    p_weeks.add_argument("--json", action="store_true", help="Output JSON")

    p_search = sub.add_parser("search", help="Search this week's dishes by name")
    p_search.add_argument("keyword", type=str, help="Part of a dish name, Chinese or English")
    add_common(p_search)

    p_all = sub.add_parser("allergens", help="List allergen codes and names")
    p_all.add_argument("--json", action="store_true", help="Output JSON")

    sub.add_parser("clear-cache", help="Delete cached API responses")
    sub.add_parser("mcp", help="Start the MCP server over stdio")

    args = parser.parse_args()

    if args.command == "mcp":
        from mcp_server import run_stdio_server
        run_stdio_server()
        return

    commands = {
        "info": cmd_info, "menu": cmd_menu, "week": cmd_week, "weeks": cmd_weeks,
        "search": cmd_search, "allergens": cmd_allergens, "clear-cache": cmd_cache,
    }
    try:
        commands.get(args.command, cmd_info)(args)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
