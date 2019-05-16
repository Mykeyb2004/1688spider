#!/usr/bin/env python
# -*- encoding=utf8 -*-

__author__ = "Minni"

from config import *
from poco_function import *

# 上页中的商品名，为检查是否在翻页后重复之用
goods_titles = []
goods_obj_list = []

def save_urls(urls):
    with open("list.txt", "w", encoding="utf-8") as file:
        file.writelines([str(x) + "\n" for x in urls])
    print("Saved!")

if __name__ == '__main__':
    pages = 3

    for i in range(1, pages):
        print(i)
        goods_obj_list = get_goods_objs(goods_titles)
        goods_titles = get_goods_title(goods_obj_list)
        print(goods_titles)
        get_detail_pages(goods_obj_list)
        if i <= (pages - 1):
            poco().scroll(percent=scroll_percent, duration=scroll_duration)
            sleep(scroll_time)
        save_urls(urls)


