# DLMenu
> A neofetch-style CLI tool to check the THISDL canteen menu from your terminal.

Data comes from the public canteen page
[MENU OF THISDL](https://pay.thishd.cn/pay/mini/index.html#/pages/nologin/canteen/index_x?id=147).
No login is needed.
---
## Installation
### 1. Install dlmenu
You can install it with a command `zsh <(curl -fsSL https://raw.githubusercontent.com/huangdihd/dlmenu/master/install.sh)`
### 2. Enjoy it!
Use command `dlmenu` to see what's for lunch anywhere!

Responses are cached in `~/.dlmenu/cache` for 30 minutes. Run `dlmenu clear-cache` to refresh
right away, or set `DLMENU_CACHE_TTL=0` to turn the cache off.

The default school is 中学. Use `-S 小学` or set `DLMENU_SCHOOL=小学` for the primary-school menu.

## MCP over stdio

DLMenu can run as an MCP server for clients such as Claude Desktop:

```bash
dlmenu mcp
```

```json
{
  "mcpServers": {
    "dlmenu": {
      "command": "/Users/you/dlmenu/.venv/bin/python3",
      "args": ["/Users/you/dlmenu/main.py", "mcp"]
    }
  }
}
```

Available tools: `get_overview`, `get_menu`, `get_week`, `search_dishes`, and `list_allergens`.
All of them are read-only.

## Uninstallation
You can uninstall it with a command `zsh <(curl -fsSL https://raw.githubusercontent.com/huangdihd/dlmenu/master/uninstall.sh)`
---
## Usage
```
dlmenu                   Neofetch-style overview of today (default)
```
### Menu
```
dlmenu menu              Show today's full menu
dlmenu menu -t           Show tomorrow's menu
dlmenu menu -D fri       Show this Friday's menu (mon..sun / 周一..周日 / 1..7)
dlmenu menu -d 2026-11-03
                         Show the menu for a specific date
dlmenu menu -m lunch supper
                         Show only some meals
                         (breakfast, morning, lunch, muslim, afternoon, supper, night)
dlmenu menu -x 花生 虾   Mark dishes containing peanut or shrimp in red
dlmenu menu -x peanut --hide
                         Hide dishes containing peanut
dlmenu menu --en         English names first
dlmenu menu -S 小学      Primary-school menu
dlmenu menu -l           Also print the web page link
```
### Week
```
dlmenu week              This week's lunch and supper main dishes at a glance
dlmenu week -n           Next week (once it is published)
dlmenu week -m breakfast lunch supper
                         Choose which meals to show
```
### Search
```
dlmenu search 鸡         Find dishes this week whose name contains 鸡
dlmenu search beef       English works too
```
### Weeks
```
dlmenu weeks             List published menu weeks and their IDs
dlmenu weeks -l 5        Only the latest 5
```
### Allergens
```
dlmenu allergens         List allergen codes with Chinese and English names
```
Add `--json` to `menu`, `week`, `weeks`, `search` or `allergens` for machine-readable output.

## How it works
The page is a Taro web app that calls two public endpoints on `https://api-mo.thishd.cn/`:

| Endpoint | Params | Returns |
| --- | --- | --- |
| `api/info/canteen_week_list` | – | Published weeks (`id`, `week_title`, `day_start` like `261026`) |
| `api/info/canteen_item_list` | `page=1&page_size=150&week_id=<id>&week=星期一..星期日&remark=中学/小学` | Dishes grouped by meal and type, with names, calories and allergen codes |

Allergen codes map to the icons at `static.thishd.cn/officialaccount/images/canteen/a/<code>.png`.
Code 16 has no icon on the server; it is assumed to be oyster sauce, the only item left in the legend.

---
**If you like this project, please give me a star!**
