#!/usr/bin/env python
# -*- encoding=utf8 -*-

__author__ = "Minni"

from config import *
from poco_function import *

# 上页中的商品名，为检查是否在翻页后重复之用
goods_titles = []
goods_obj_list = []


def save_list(filename, list):
    with open(filename, "w", encoding="utf-8") as file:
        file.writelines([str(x) + "\n" for x in list])


if __name__ == '__main__':
    scroll_pages = 1

    print(exec_cmd((adb_run_clipper)))

    while True:
        print("第{}次滚动翻页：".format(scroll_pages))
        goods_obj_list = get_goods_objs(goods_titles)
        goods_titles = get_goods_title(goods_obj_list)

        print("本页发现商品:{}个：{}".format(len(goods_titles), goods_titles))
        get_detail_pages(goods_obj_list)
        save_list("list.txt", urls)
        save_list("missing.txt", missing_goods)

        if not is_ending():
            scroll_pages += 1
            poco().scroll(percent=scroll_percent, duration=scroll_duration)
        else:
            break

        # 调试时限制翻页数用，正式运行时记得注释掉
        if scroll_pages >= 2:
            break

    print("It's DONE!\n {} records saved, {} records missed.".format(len(urls), len(missing_goods)))
