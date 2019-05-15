#!/usr/bin/env python
# -*- encoding=utf8 -*-

__author__ = "Minni"

from config import *
from poco_function import *

# 上页中的商品名，为检查是否在翻页后重复之用
goods_titles = []
goods_obj_list = []

if __name__ == '__main__':
    for i in range(1, 3):
        print(i)
        goods_obj_list = get_goods_objs(goods_titles)
        goods_titles = get_goods_title(goods_obj_list)
        print(goods_titles)
        poco().scroll(percent=scroll_percent, duration=scroll_duration)
        sleep(scroll_time)
    print(goods_titles[-1])
