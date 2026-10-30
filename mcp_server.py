import os
import re
import subprocess
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

SERVER_NAME = "dlmenu"
PROJECT_ROOT = Path(__file__).resolve().parent
ANSI_ESCAPE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")

mcp = FastMCP(SERVER_NAME)


def _run_dlmenu(arguments: list[str], timeout: int = 120) -> str:
    environment = os.environ.copy()
    environment["DLMENU_NONINTERACTIVE"] = "1"
    completed = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "main.py"), *arguments],
        cwd=PROJECT_ROOT, env=environment, capture_output=True, text=True, timeout=timeout,
    )
    output = ANSI_ESCAPE.sub("", completed.stdout).strip()
    if completed.returncode == 0:
        return output
    error = ANSI_ESCAPE.sub("", completed.stderr).strip()
    raise RuntimeError(output or error or f"dlmenu exited with status {completed.returncode}")


def _date_args(date: str | None, tomorrow: bool, weekday: str | None) -> list[str]:
    if sum((date is not None, tomorrow, weekday is not None)) > 1:
        raise ValueError("Only one of date, tomorrow, and weekday may be supplied")
    if date:
        return ["--date", date]
    if tomorrow:
        return ["--tomorrow"]
    if weekday:
        return ["--day", weekday]
    return []


@mcp.tool()
def get_overview(school: str | None = None) -> str:
    """Today's canteen overview: dish counts per meal and the next meal's main dishes.

    Args:
        school: "中学" (default) or "小学".
    """
    return _run_dlmenu(["info", *(["--school", school] if school else [])])


@mcp.tool()
def get_menu(
    date: str | None = None,
    tomorrow: bool = False,
    weekday: str | None = None,
    meals: list[str] | None = None,
    school: str | None = None,
    exclude_allergens: list[str] | None = None,
) -> str:
    """Get one day's full canteen menu as JSON (names in Chinese and English, calories, allergens).

    Args:
        date: A date in YYYY-MM-DD format. Defaults to today.
        tomorrow: Use tomorrow instead of today.
        weekday: A day of the current week, e.g. "fri", "周五" or "5".
        meals: Only these meals: breakfast, morning, lunch, muslim, afternoon, supper, night.
        school: "中学" (default) or "小学".
        exclude_allergens: Hide dishes containing these allergens (Chinese name, English name or code).
    """
    arguments = ["menu", "--json", *_date_args(date, tomorrow, weekday)]
    if meals:
        arguments.extend(["--meal", *meals])
    if school:
        arguments.extend(["--school", school])
    if exclude_allergens:
        arguments.extend(["--exclude", *exclude_allergens, "--hide"])
    return _run_dlmenu(arguments)


@mcp.tool()
def get_week(next_week: bool = False, school: str | None = None) -> str:
    """Get the whole week's canteen menu as JSON.

    Args:
        next_week: Get next week's menu (if it has been published).
        school: "中学" (default) or "小学".
    """
    arguments = ["week", "--json"]
    if next_week:
        arguments.append("--next")
    if school:
        arguments.extend(["--school", school])
    return _run_dlmenu(arguments)


@mcp.tool()
def search_dishes(keyword: str, school: str | None = None) -> str:
    """Find which days and meals this week serve a dish whose name contains the keyword (Chinese or English)."""
    return _run_dlmenu(["search", keyword, "--json", *(["--school", school] if school else [])])


@mcp.tool()
def list_allergens() -> str:
    """List allergen codes with their Chinese and English names."""
    return _run_dlmenu(["allergens", "--json"])


def run_stdio_server() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_stdio_server()
