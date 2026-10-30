# -*- coding: utf-8 -*-
from api import clear_cache, CACHE_DIR


def cmd_cache(args):
    n = clear_cache()
    print(f"已清除 {n} 个缓存文件（{CACHE_DIR}）")
