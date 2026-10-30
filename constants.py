# -*- coding: utf-8 -*-
API_BASE = "https://api-mo.thishd.cn/"
WEB_URL = "https://pay.thishd.cn/pay/mini/index.html#/pages/nologin/canteen/index_x?id={week_id}"
HEADERS = {
    "Content-Type": "application/json",
    "Client": "web_mini",
    "User-Agent": "dlmenu (+https://github.com/huangdihd/dlmenu)",
}

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
ORANGE = "\033[38;5;208m"

logo = [
    f"{ORANGE}     ( (    {RESET}",
    f"{ORANGE}      ) )   {RESET}",
    f"{YELLOW}  .-------. {RESET}",
    f"{YELLOW}  |       |]{RESET}",
    f"{YELLOW}  \\       / {RESET}",
    f"{YELLOW}   `-----'  {RESET}",
    f"{ORANGE}  THISDL    {RESET}",
    f"{ORANGE}  CANTEEN   {RESET}",
]

WEEKDAYS_CN = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
WEEKDAYS_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# 页面上的“小学 / 中学”切换，对应接口里的 remark 参数
SCHOOLS = {"中学": "中学", "middle": "中学", "high": "中学", "m": "中学",
           "小学": "小学", "primary": "小学", "p": "小学"}

# 菜品类别（接口字段后缀 -> 中文 / 英文），中英文取自页面里的 dishTypeEn
DISH_TYPES = {
    "meat_or_fish_dish": ("荤菜", "Meat or fish dish"),
    "half_meat_dish": ("半荤菜", "Half meat dish"),
    "egg_dish": ("蛋类菜", "Egg dish"),
    "vegetable_dish": ("素菜", "Vegetable dish"),
    "staple_food": ("主食", "Staple food"),
    "local_flavours": ("小吃", "Local flavours"),
    "coarse_cereals": ("杂粮", "Coarse cereals"),
    "pizza": ("披萨", "Pizza"),
    "chinese_style": ("中式", "Chinese style"),
    "western_style": ("西式", "Western style"),
    "western_cake": ("西点", "Western cake"),
    "eggs": ("蛋类", "Eggs"),
    "side_dish": ("小菜", "Side dish"),
    "liquid_diet": ("流食", "Liquid diet"),
    "soup_congee": ("汤&粥", "Soup&Congee"),
    "fruit": ("水果", "Fruit"),
    "drink": ("饮品", "Drink"),
}

# 餐次：key, 中文, 英文, 接口字段前缀（或完整字段名）, 颜色, 大致开始时间
MEALS = [
    ("breakfast", "早餐", "Breakfast", "breakfast_", YELLOW, "07:00"),
    ("morning", "上午加餐", "Morning snacks", "morning_snacks", MAGENTA, "10:00"),
    ("lunch", "午餐", "Lunch", "lunch_", GREEN, "11:30"),
    ("muslim", "清真午餐", "Muslim lunch", "muslim_lunch", CYAN, "11:30"),
    ("afternoon", "下午加餐", "Afternoon snacks", "afternoon_snacks", MAGENTA, "15:30"),
    ("supper", "晚餐", "Supper", "supper_", BLUE, "17:30"),
    ("night", "夜宵", "Night meal", "night_meal", RED, "20:30"),
]

# 过敏原编号 -> (中文, 英文)。编号对应 static.thishd.cn/.../canteen/a/<编号>.png，
# 英文名来自页面的过敏原图例 gmhuizong.jpg。12、16 号图标在服务器上不存在；
# 12 号出现在“苹果”上，确定是水果；16 号是图例中剩下的唯一一项，推测为蚝油。
ALLERGENS = {
    1: ("禽类", "Poultry"),
    2: ("牛羊", "Cattle and Sheep"),
    3: ("猪肉", "Pork"),
    4: ("全谷物", "Whole grains"),
    5: ("小麦", "Wheat"),
    6: ("酵母", "Yeast"),
    7: ("鸡蛋", "Egg"),
    8: ("竹笋", "Bamboo shoots"),
    9: ("植物油", "Vegetable oil"),
    10: ("植物调料", "Plant seasoning"),
    11: ("干果", "Dried Fruit"),
    12: ("水果", "Fruit"),
    13: ("胡椒", "Pepper"),
    14: ("酱料", "Sauce"),
    15: ("果酱", "Jam"),
    16: ("蚝油?", "Oyster sauce?"),
    17: ("酱油", "Soy sauce"),
    18: ("乳制品", "Dairy"),
    19: ("牛奶", "Milk"),
    20: ("豆制品", "Soy Products"),
    21: ("海藻类", "Sea vegetables"),
    22: ("海鲜", "Seafood"),
    23: ("花生", "Peanut"),
    24: ("可可豆", "Cocoa beans"),
    25: ("菌菇", "Mushroom"),
    26: ("花", "Flower"),
    27: ("肉松", "Meat floss"),
    28: ("香菜", "Coriander"),
    29: ("蔬菜", "Vegetable"),
    30: ("蒜", "Spicy garlic"),
    31: ("土豆", "Potatoes"),
    32: ("虾", "Shrimp"),
    33: ("鱼", "Fish"),
}
