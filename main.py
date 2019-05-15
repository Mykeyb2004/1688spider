#!/usr/bin/env python
# -*- encoding=utf8 -*-

__author__ = "Minni"

from config import *
from poco_function import *

# 上页中的商品名，为检查是否在翻页后重复之用
last_goods_title = []
last_goods_obj_list = []

if __name__ == '__main__':
    for i in range(1, 3):
        print(i)
        last_goods_title, last_goods_obj_list = get_goods_title(last_goods_title)
        print(last_goods_title)
        print(last_goods_obj_list)
        poco().scroll(percent=scroll_percent, duration=scroll_duration)
        sleep(scroll_time)
