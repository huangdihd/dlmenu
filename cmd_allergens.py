# -*- coding: utf-8 -*-
from constants import ALLERGENS, BOLD, DIM
from utils import c, pad, dump_json


def cmd_allergens(args):
    if args.json:
        dump_json([{"code": k, "name": v[0], "name_en": v[1]} for k, v in ALLERGENS.items()])
        return
    print(c("过敏原编号 Allergens", BOLD))
    items = list(ALLERGENS.items())
    for i in range(0, len(items), 3):
        row = [pad(f"{k:>2}  {cn}", 14) + pad(en, 18) for k, (cn, en) in items[i:i + 3]]
        print("  " + "".join(row))
    print(c("  使用 -x 排除含某过敏原的菜，例如: dlmenu menu -x 花生 虾", DIM))
